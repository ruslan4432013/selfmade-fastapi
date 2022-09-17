from aioWebWolf.core import Engine, Logger
from aioWebWolf.utils import create_response
from aioWebWolf.utils.responses import template_response

site = Engine()
logger = Logger('main')


class Index:
    async def __call__(self, request):
        return template_response('main/index.jinja2')


class Courses:
    async def __call__(self, request):
        return template_response('main/course.jinja2', objects_list=site.categories)


class About:
    async def __call__(self, request):
        return template_response('main/about.jinja2')


class Contacts:
    async def __call__(self, request):
        return template_response('main/contacts.jinja2')


class CoursesList:
    async def __call__(self, request):
        logger.log('Список курсов')
        try:
            category_id = int(request['request_params']['id'])
            category = site.find_category_by_id(category_id)
            context = dict(
                objects_list=category.courses,
                name=category.name,
                id=category_id
            )

            return template_response('main/course_list.jinja2', **context)
        except KeyError:
            return create_response(200, 'No courses have been added yet')


class CreateCourse:
    category_id = -1

    async def __call__(self, request):
        if request['method'] == 'POST':
            data = request['data']
            name = data['name']
            category = None
            if self.category_id != -1:
                category = site.find_category_by_id(int(self.category_id))
                course = site.create_course('record', name, category)
                site.courses.append(course)

            context = dict(
                objects_list=category.courses,
                name=category.name,
                id=category.id
            )
            return template_response('main/course_list.jinja2', **context)

        else:
            try:
                self.category_id = int(request['request_params']['id'])

                category = site.find_category_by_id(self.category_id)

                return template_response('main/create_course.jinja2',
                                         name=category.name,
                                         id=category.id)
            except KeyError:
                return create_response(200, 'No courses have been added yet')


class CreateCategory:
    async def __call__(self, request):

        if request['method'] == 'POST':

            data = request['data']

            name = data['name']

            category_id = data.get('category_id')

            category = None
            if category_id:
                category = site.find_category_by_id(int(category_id))

            new_category = site.create_category(name, category)

            site.categories.append(new_category)

            return template_response('main/course.jinja2', objects_list=site.categories)
        else:
            categories = site.categories
            return template_response('main/create_category.jinja2', categories=categories)


class CategoryList:
    async def __call__(self, request):
        logger.log('Список категорий')
        return template_response('main/category_list.jinja2',
                                 objects_list=site.categories)


class CopyCourse:
    async def __call__(self, request):
        request_params = request['request_params']

        try:
            name = request_params['name']

            old_course = site.get_course(name)
            if old_course:
                new_name = f'copy_{name}'
                new_course = old_course.clone()
                new_course.name = new_name
                site.courses.append(new_course)
            else:
                raise Exception('Нет такого курса, что-то не так')

            return template_response('main/course_list.jinja2',
                                     objects_list=site.courses,
                                     name=new_course.category.name)
        except KeyError:
            return create_response(200, 'No courses have been added yet')
