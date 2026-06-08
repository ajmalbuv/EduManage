import math
from datetime import date, timedelta

from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.signals import post_delete, post_save

# Create your models here.
sex_choice = (("Male", "Male"), ("Female", "Female"))

time_slots = (
    ("8:30 - 9:45", "8:30 - 9:45"),
    ("9:45 - 10:45", "9:45 - 10:45"),
    ("11:10 - 12:10", "11:10 - 12:10"),
    ("12:10 - 1:10", "12:10 - 1:10"),
    ("1:50 - 2:40", "1:50 - 2:40"),
    ("2:40 - 3:30", "2:40 - 3:30"),
)

DAYS_OF_WEEK = (
    ("Monday", "Monday"),
    ("Tuesday", "Tuesday"),
    ("Wednesday", "Wednesday"),
    ("Thursday", "Thursday"),
    ("Friday", "Friday"),
    ("Saturday", "Saturday"),
)

test_name = (
    ("Internal test 1", "Internal test 1"),
    ("Internal test 2", "Internal test 2"),
    ("Assignment 1", "Assignment 1"),
    ("Assignment 2", "Assignment 2"),
    ("Semester End Exam", "Semester End Exam"),
)


class User(AbstractUser):
    @property
    def is_student(self):
        if hasattr(self, "student"):
            return True
        return False

    @property
    def is_teacher(self):
        if hasattr(self, "teacher"):
            return True
        return False


class Dept(models.Model):
    id = models.CharField(primary_key="True", max_length=100)
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Course(models.Model):
    dept = models.ForeignKey(Dept, on_delete=models.CASCADE)
    id = models.CharField(primary_key="True", max_length=50)
    name = models.CharField(max_length=50)
    shortname = models.CharField(max_length=50, default="X")

    def __str__(self):
        return self.name


class Class(models.Model):
    # courses = models.ManyToManyField(Course, default=1)
    id = models.CharField(primary_key="True", max_length=100)
    dept = models.ForeignKey(Dept, on_delete=models.CASCADE)
    section = models.CharField(max_length=100)
    sem = models.IntegerField()

    class Meta:
        verbose_name_plural = "classes"

    def __str__(self):
        d = Dept.objects.get(name=self.dept)
        return "%s : %d %s" % (d.name, self.sem, self.section)


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    class_id = models.ForeignKey(Class, on_delete=models.CASCADE, default=1)
    USN = models.CharField(primary_key="True", max_length=100)
    name = models.CharField(max_length=200)
    sex = models.CharField(max_length=50, choices=sex_choice, default="Male")
    DOB = models.DateField(default="1998-01-01")

    def __str__(self):
        return self.name


class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    id = models.CharField(primary_key=True, max_length=100)
    dept = models.ForeignKey(Dept, on_delete=models.CASCADE, default=1)
    name = models.CharField(max_length=100)
    sex = models.CharField(max_length=50, choices=sex_choice, default="Male")
    DOB = models.DateField(default="2001-01-01")

    def __str__(self):
        return self.name


class Assign(models.Model):
    class_id = models.ForeignKey(Class, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)

    class Meta:
        unique_together = (("course", "class_id", "teacher"),)

    def __str__(self):
        cl = Class.objects.get(id=self.class_id_id)
        cr = Course.objects.get(id=self.course_id)
        te = Teacher.objects.get(id=self.teacher_id)
        return "%s : %s : %s" % (te.name, cr.shortname, cl)


class AssignTime(models.Model):
    assign = models.ForeignKey(Assign, on_delete=models.CASCADE)
    period = models.CharField(
        max_length=50, choices=time_slots, default="11:10 - 12:10"
    )
    day = models.CharField(max_length=15, choices=DAYS_OF_WEEK)


class AttendanceClass(models.Model):
    assign = models.ForeignKey(Assign, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.IntegerField(default=0)

    class Meta:
        verbose_name = "Attendance"
        verbose_name_plural = "Attendance"


class Attendance(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    attendanceclass = models.ForeignKey(
        AttendanceClass, on_delete=models.CASCADE, default=1
    )
    date = models.DateField(default="2024-05-01")
    status = models.BooleanField(default="True")

    def __str__(self):
        sname = Student.objects.get(name=self.student)
        cname = Course.objects.get(name=self.course)
        return "%s : %s" % (sname.name, cname.shortname)


class AttendanceTotal(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)

    class Meta:
        unique_together = (("student", "course"),)

    @property
    def att_class(self):
        stud = Student.objects.get(name=self.student)
        cr = Course.objects.get(name=self.course)
        att_class = Attendance.objects.filter(
            course=cr, student=stud, status="True"
        ).count()
        return att_class

    @property
    def total_class(self):
        stud = Student.objects.get(name=self.student)
        cr = Course.objects.get(name=self.course)
        total_class = Attendance.objects.filter(course=cr, student=stud).count()
        return total_class

    @property
    def attendance(self):
        stud = Student.objects.get(name=self.student)
        cr = Course.objects.get(name=self.course)
        total_class = Attendance.objects.filter(course=cr, student=stud).count()
        att_class = Attendance.objects.filter(
            course=cr, student=stud, status="True"
        ).count()
        if total_class == 0:
            attendance = 0
        else:
            attendance = round(att_class / total_class * 100, 2)
        return attendance

    @property
    def classes_to_attend(self):
        stud = Student.objects.get(name=self.student)
        cr = Course.objects.get(name=self.course)
        total_class = Attendance.objects.filter(course=cr, student=stud).count()
        att_class = Attendance.objects.filter(
            course=cr, student=stud, status="True"
        ).count()
        cta = math.ceil((0.75 * total_class - att_class) / 0.25)
        if cta < 0:
            return 0
        return cta


class StudentCourse(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    class Meta:
        unique_together = (("student", "course"),)
        verbose_name_plural = "Marks"

    def __str__(self):
        sname = Student.objects.get(name=self.student)
        cname = Course.objects.get(name=self.course)
        return "%s : %s" % (sname.name, cname.shortname)

    def get_cie(self):
        # Fetch the marks for assignments and internal tests
        assignment_1_marks = self.marks_set.filter(name="Assignment 1").first().marks1
        assignment_2_marks = self.marks_set.filter(name="Assignment 2").first().marks1
        internal_1_marks = self.marks_set.filter(name="Internal test 1").first().marks1
        internal_2_marks = self.marks_set.filter(name="Internal test 2").first().marks1

        # Convert assignment marks to a value out of 40
        assignment_1_converted = (assignment_1_marks / 20) * 40
        assignment_2_converted = (assignment_2_marks / 20) * 40

        # Calculate the total CIE marks out of 40
        cie_total = math.ceil(
            (
                assignment_1_converted
                + assignment_2_converted
                + internal_1_marks
                + internal_2_marks
            )
            / 4
        )
        return cie_total

    def get_attendance(self):
        a = AttendanceTotal.objects.get(student=self.student, course=self.course)
        return a.attendance


class Marks(models.Model):
    studentcourse = models.ForeignKey(StudentCourse, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, choices=test_name, default="Internal test 1")
    marks1 = models.IntegerField(
        default=0, validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    class Meta:
        unique_together = (("studentcourse", "name"),)

    @property
    def total_marks(self):
        if self.name == "Semester End Exam":
            return 60
        elif self.name == "Assignment 1":
            return 20
        elif self.name == "Assignment 2":
            return 20
        return 40


class MarksClass(models.Model):
    assign = models.ForeignKey(Assign, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, choices=test_name, default="Internal test 1")
    status = models.BooleanField(default="False")

    class Meta:
        unique_together = (("assign", "name"),)

    @property
    def total_marks(self):
        if self.name == "Semester End Exam":
            return 60
        elif self.name == "Assignment 1":
            return 20
        elif self.name == "Assignment 2":
            return 20
        return 40


class AttendanceRange(models.Model):
    start_date = models.DateField()
    end_date = models.DateField()


# Triggers


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


days = {
    "Monday": 1,
    "Tuesday": 2,
    "Wednesday": 3,
    "Thursday": 4,
    "Friday": 5,
    "Saturday": 6,
}


def create_attendance(sender, instance, **kwargs):
    if kwargs.get("created"):
        attendance_range = AttendanceRange.objects.first()
        if not attendance_range:
            # Create a default range if none exists
            today = date.today()
            attendance_range = AttendanceRange.objects.create(
                start_date=today, end_date=today + timedelta(weeks=20)
            )

        start_date = attendance_range.start_date
        end_date = attendance_range.end_date
        target_day = days.get(instance.day)

        if target_day is None:
            return

        # Fetch existing dates to avoid duplicates
        existing_dates = set(
            AttendanceClass.objects.filter(assign=instance.assign).values_list(
                "date", flat=True
            )
        )

        new_classes = []
        for single_date in daterange(start_date, end_date):
            if single_date.isoweekday() == target_day:
                if single_date not in existing_dates:
                    new_classes.append(
                        AttendanceClass(
                            date=single_date, assign=instance.assign, status=0
                        )
                    )

        if new_classes:
            AttendanceClass.objects.bulk_create(new_classes)


def create_marks(sender, instance, **kwargs):
    if kwargs.get("created"):
        if isinstance(instance, Student):
            assigns = instance.class_id.assign_set.all()
            for ass in assigns:
                sc, created = StudentCourse.objects.get_or_create(
                    student=instance, course=ass.course
                )
                if created:
                    Marks.objects.bulk_create(
                        [Marks(studentcourse=sc, name=name[0]) for name in test_name]
                    )
        elif isinstance(instance, Assign):
            students = instance.class_id.student_set.all()
            for s in students:
                sc, created = StudentCourse.objects.get_or_create(
                    student=s, course=instance.course
                )
                if created:
                    Marks.objects.bulk_create(
                        [Marks(studentcourse=sc, name=name[0]) for name in test_name]
                    )


def create_marks_class(sender, instance, **kwargs):
    if kwargs["created"]:
        for name in test_name:
            try:
                MarksClass.objects.get(assign=instance, name=name[0])
            except MarksClass.DoesNotExist:
                m = MarksClass(assign=instance, name=name[0])
                m.save()


def delete_marks(sender, instance, **kwargs):
    stud_list = instance.class_id.student_set.all()
    StudentCourse.objects.filter(course=instance.course, student__in=stud_list).delete()


post_save.connect(create_marks, sender=Student)
post_save.connect(create_marks, sender=Assign)
post_save.connect(create_marks_class, sender=Assign)
post_save.connect(create_attendance, sender=AssignTime)
post_delete.connect(delete_marks, sender=Assign)
